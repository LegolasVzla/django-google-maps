-- DROP FUNCTION public.udf_spots_nearby_within_X_kilometers_from_current_user_position(integer, double precision, double precision);
CREATE OR REPLACE FUNCTION public.udf_spots_nearby_within_X_kilometers_from_current_user_position(
    param_user_id integer,
    param_lat double precision,
    param_long double precision)
  RETURNS json AS
$BODY$

DECLARE

  local_max_distance decimal = 5000.0;    -- Default max distance: 5 km or you could receive it as a parameter
  aux_tree_returning varchar = '';
  param_json_returning json := '[{
      "spotId": null,
      "spotName": null,
      "lat": null,
      "lng": null,
      "country": null,
      "city": null,
      "is_active": null,
      "imageList": []
    }]';
  --i RECORD;
    
  BEGIN        

  /*
  -- To Test:
    SELECT udf_spots_nearby_within_X_kilometers_from_current_user_position(1,10.4823307,-66.861713);
  */

  -- Prevention SQL injection
  IF NOT EXISTS(
    SELECT
      id
    FROM
      public.users_customuser
    WHERE
      id = param_user_id
    ) THEN

    RAISE NOTICE 'User % not found',param_user_id;
    RETURN param_json_returning;

  END IF;

  -- Create a temporary table to store nearby places
  CREATE TEMPORARY TABLE IF NOT EXISTS temporal_spots_table (
        id integer,
        name character varying,
        lat double precision,
        lng double precision,
        country character varying,
        country_code character varying,        
        city character varying,
        is_active boolean DEFAULT true,
        is_deleted boolean DEFAULT false
  );

  INSERT INTO temporal_spots_table(
    id,
    name,
    lat,
    lng,
    country,
    country_code,
    city,
    is_active,
    is_deleted
  )

  -- This is the main query:
  -- Get the places within 5 km from the current position where you are, using PostGIS
  SELECT
    s.id,
    s.name,
    s.lat,
    s.lng,
    s.country,
    s.country_code,
    s.city,
    s.is_active,
    s.is_deleted
  FROM
    public.api_spots s
    INNER JOIN public.users_customuser uc
      ON uc.id = s.user_id
  WHERE
    s.user_id = param_user_id
    --AND 
    --s.lat != param_lat
    --AND
    --s.lng != param_long
    AND
    s.is_active
    AND
    uc.is_active
    AND
    NOT s.is_deleted
    AND
    NOT uc.is_deleted
    AND
    ST_DistanceSphere("s"."position", ST_GeomFromEWKB(ST_MakePoint(param_long,param_lat)::bytea)) <= (local_max_distance::float);

    -- Only for temporal_spots_table test purpose 
    /*
    FOR i IN (
      SELECT *
      FROM
        temporal_spots_table
      ) LOOP

      RAISE NOTICE 'spot_id: %',i.id;

    END LOOP;
    */

  IF EXISTS (
    SELECT
      id
    FROM
      temporal_spots_table
    ) THEN

      --RAISE NOTICE 'Were found places near where you are';

      SELECT JSON_AGG(a.*) INTO STRICT aux_tree_returning
      FROM (
        SELECT
          tst.id "spotId",
          tst.name "spotName",
          tst.lat,
          tst.lng,
          tst.country,
          tst.country_code,
          tst.city,
          tst.is_active,    
          tst.is_deleted,
          (select public.udf_images_get(tst.id) as "imageList")
        FROM 
          temporal_spots_table tst     
      )a;

        param_json_returning = (replace(aux_tree_returning, '\"', ''))::json;

  ELSE

    --RAISE NOTICE 'Were not found places near where you are';

  END IF;

    RETURN param_json_returning;

  DROP TABLE IF EXISTS temporal_spots_table;
  --COMMIT;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.udf_spots_nearby_within_X_kilometers_from_current_user_position(integer, double precision, double precision)
  OWNER TO postgres;